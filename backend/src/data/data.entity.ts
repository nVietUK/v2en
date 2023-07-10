import { ObjectType } from '@nestjs/graphql';
import { Md5 } from 'ts-md5';
import { Column, Entity, PrimaryColumn, PrimaryGeneratedColumn } from 'typeorm';
import { DataInput } from './data.dto';
import { Injectable } from '@nestjs/common';
import { DataService } from './data.service';
import { GraphQLError } from 'graphql';

@Entity()
@ObjectType('DataObject')
@Injectable()
export class Data {
	constructor(
		origin = '',
		translated = '',
		translator = '',
		verified = false,
		dataService: DataService,
	) {
		this.origin = origin;
		this.translated = translated;
		this.translator = translator;
		this.verified = verified;
		this.validate(dataService);
	}

	static fromDataInput(data: DataInput, dataService: DataService) {
		return new Data(
			data.origin,
			data.translated,
			data.translator,
			data.verified,
			dataService,
		);
	}

	@PrimaryGeneratedColumn()
	@PrimaryColumn('int')
	id?: number;

	@Column('longtext')
	origin: string;

	@Column('longtext')
	translated: string;

	@Column('longtext')
	translator: string;

	@Column('longtext', { nullable: false })
	get hashValue(): string {
		return Md5.hashStr(
			`${this.origin} ${this.translated} ${this.translator}`,
		).toString();
	}
	set hashValue(value: string) {
		value;
	}

	@Column({ default: false })
	verified: boolean;

	private validate(dataService: DataService) {
		const result = dataService?.findOneBy({
			hashValue: this.hashValue,
		});
		if (result != null) {
			throw new GraphQLError('Data is existed', {
				extensions: {
					code: 'BAD_USER_INPUT',
				},
			});
		}
	}
}

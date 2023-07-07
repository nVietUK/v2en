import { Field, InputType, ObjectType } from '@nestjs/graphql';
import { Md5 } from 'ts-md5';
import { Column, Entity, PrimaryColumn, PrimaryGeneratedColumn } from 'typeorm';

@Entity()
@ObjectType('DataObject')
@InputType('DataInput')
export class Data {
	constructor(origin = '', translated = '', translator = '', verified = false) {
		this.origin = origin;
		this.translated = translated;
		this.translator = translator;
		this.verified = verified;
	}

	@PrimaryGeneratedColumn()
	@PrimaryColumn('int')
	id?: number;

	@Field(() => String, { description: 'the origin of sentence' })
	@Column('longtext')
	origin: string;

	@Column('longtext')
	@Field(() => String, { description: 'the translated of sentence' })
	translated: string;

	@Column('longtext')
	@Field(() => String, { description: "the sentence's translator" })
	translator: string;

	@Column('longtext', { nullable: false })
	get hashValue(): string {
		return Md5.hashStr(`${this.origin} ${this.translated} ${this.translator}`);
	}

	@Column({ default: false })
	@Field(() => Boolean, { description: 'confirm that data is verified by authorizer' })
	verified: boolean;
}

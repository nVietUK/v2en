import { ObjectType } from '@nestjs/graphql';
import { Md5 } from 'ts-md5';
import { Column, Entity, PrimaryGeneratedColumn } from 'typeorm';
import { UserInput } from './user.dto';

@Entity()
@ObjectType('UserObject')
export class User {
	constructor(
		username = '',
		familyName = '',
		givenName = '',
		gender = '',
		birthDay: Date = new Date(0, 0, 0),
		password = '',
	) {
		this.username = username;
		this.familyName = familyName;
		this.givenName = givenName;
		this.password = password;
		this.gender = gender;
		this.birthDay = birthDay;
	}

	static fromUserInput(user: UserInput) {
		return new User(
			user.username,
			user.familyName,
			user.givenName,
			user.gender,
			user.birthDay,
			user.password,
		);
	}

	@PrimaryGeneratedColumn('uuid')
	id?: number;

	@Column('text')
	username: string;

	@Column('text')
	familyName: string;

	@Column('text')
	givenName: string;

	@Column('date')
	birthDay?: Date;

	@Column('text')
	gender?: string;

	@Column('text')
	hashedPassword!: string;
	set password(value: string) {
		this.hashedPassword = Md5.hashStr(value);
	}
}

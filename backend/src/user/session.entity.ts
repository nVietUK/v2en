import { Entity, PrimaryGeneratedColumn, Column, ManyToOne } from 'typeorm';
import { User } from './user.entity';
import { ObjectType } from '@nestjs/graphql';

@Entity()
@ObjectType()
export class Session {
    constructor(token: string, user: User) {
        this.token = token;
        this.user = user;
    }
    @PrimaryGeneratedColumn()
    id!: number;

    @Column()
    token!: string;

    @ManyToOne(() => User, user => user.sessions)
    user!: User;
}